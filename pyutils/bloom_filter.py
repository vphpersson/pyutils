# Heavily inspired by python-bloomfilter.

from __future__ import annotations
from struct import pack as struct_pack, unpack_from as struct_unpack_from, Struct, calcsize as struct_calcsize
from math import ceil, log
from functools import cached_property
from collections.abc import Sized, Container
from typing import SupportsBytes, Callable, Generator, Iterable, Tuple, Collection, List
import hashlib

from bitarray import bitarray


class _BitIndexNumberStruct(Struct):

    def __init__(self, num_slice_bits: int):
        """
        Initialize a `Struct` to be used for unpacking bit index numbers from a hash.

        :param num_slice_bits: The number of bits in a slice, which determines the format code.
        """

        # Q: 0 <= x <= 18446744073709551615
        # I: 0 <= x <= 4294967295
        # H: 0 <= x <= 65535

        if num_slice_bits >= (1 << 31):
            format_code = 'Q'
        elif num_slice_bits >= (1 << 15):
            format_code = 'I'
        else:
            format_code = 'H'

        super().__init__(format=format_code)


def _make_aggregated_hash_function(
    num_slices: int,
    num_bits_per_slice: int,
    hash_function=hashlib.sha3_256
) -> Callable[[bytes], Generator[int, None, None]]:
    """
    Make a customized aggregated hash function that yields bit index numbers into Bloom filter slices.

    The necessary size of the bit index number type is chosen based on the input parameters.

    :param num_slices: The number of slices that the Bloom filter uses.
    :param num_bits_per_slice: The number of bits in each of the slices that the Bloom filter uses.
    :param hash_function: The underlying hash function to be used.
    :return: A customized aggregated hash function.
    """

    # Choose the smallest struct type that can index all bits in a slice.
    # NOTE: The chosen struct type is very possibly able to store larger numbers than the number of bits per slice. To
    # take that into account, unpacked numbers are transformed with the modulo operator. If the number of bits per slice
    # does not evenly divide the maximum struct type value, the distribution will not be truly uniform.
    bit_index_number_struct: Struct = _BitIndexNumberStruct(num_slice_bits=num_bits_per_slice)

    # The struct type size may not evenly divide the resulting hash size; determine the number of bit index numbers that
    # fit into the hash.
    num_bit_index_numbers_in_hash = hash_function().digest_size // bit_index_number_struct.size

    # Use as many hash functions as are necessary to assure that each slice is indexed. Each hash function must be
    # salted as to make them independent.
    num_different_hash_functions = ceil(num_slices / num_bit_index_numbers_in_hash)
    salt_values = tuple(struct_pack('I', i) for i in range(num_different_hash_functions))

    def aggregated_hash_function(value: bytes):

        num_bit_indices_provided = 0

        for salt_value in salt_values:
            hash_value: bytes = hash_function(salt_value + value).digest()

            for hash_offset_index in range(num_bit_index_numbers_in_hash):
                yield bit_index_number_struct.unpack_from(
                    buffer=hash_value,
                    offset=hash_offset_index * bit_index_number_struct.size
                )[0] % num_bits_per_slice

                num_bit_indices_provided += 1
                if num_bit_indices_provided == num_slices:
                    return

    return aggregated_hash_function


class BloomFilter(Sized, Container):

    _IMPORT_EXPORT_LENGTH_FORMAT = '>Q'

    def __init__(
        self,
        capacity: int,
        false_positive_probability: float = 0.001,
        hash_function=hashlib.sha3_256,
        bit_array: bitarray = None
    ):
        """
        The bit size of the Bloom filter is calculated based on the requested capacity and false positive probability
        rate.

        The provided hash function will be salted in order to simulate different hash functions.

        :param capacity: The maximum number of elements to be mapped.
        :param false_positive_probability: The accepted false positive probability rate.
        :param hash_function: The underlying hash function to be used.
        """

        self._capacity = capacity
        self._false_positive_probability = false_positive_probability
        self._hash_function = hash_function

        self._num_elements_mapped = 0

        self._hash: Callable[[bytes], Generator[int, None, None]] = _make_aggregated_hash_function(
            num_slices=self.num_slices,
            num_bits_per_slice=self.num_bits_per_slice,
            hash_function=self._hash_function
        )

        self._bit_array = bitarray(self.bit_size)
        self._bit_array.setall(False)

        if bit_array:
            self._bit_array |= bit_array[:len(self._bit_array)]

    @classmethod
    def from_values(
        cls,
        values: Iterable[SupportsBytes],
        capacity: int,
        false_positive_probability: float = 0.001,
        hash_function=hashlib.sha3_256
    ) -> BloomFilter:
        """
        Make a Bloom filter from an iterable of values, using a provided capacity.

        :param values: The values to be added to the Bloom filter.
        :param capacity: The maximum number of elements to be mapped.
        :param false_positive_probability: The accepted false positive probability rate.
        :param hash_function: The underlying hash function to be used.
        :return: A Bloom filter initialized with the provided entries.
        """

        bloom_filter = cls(
            capacity=capacity,
            false_positive_probability=false_positive_probability,
            hash_function=hash_function
        )
        bloom_filter.update(*values)

        return bloom_filter

    @classmethod
    def from_values_2(
        cls,
        values: Collection[SupportsBytes],
        capacity_proportion: float = 1.5,
        false_positive_probability: float = 0.001,
        hash_function=hashlib.sha3_256
    ) -> BloomFilter:
        """
        Make a Bloom filter from a collection of values, using a provided capacity proportion.

        :param values: The values to be added to the Bloom filter.
        :param capacity_proportion: The capacity as a proportion to the provided entries.
        :param false_positive_probability: The accepted false positive probability rate.
        :param hash_function: The underlying hash function to be used.
        :return: A Bloom filter initialized with the provided entries.
        """

        bloom_filter = cls(
            capacity=ceil(capacity_proportion * len(values)),
            false_positive_probability=false_positive_probability,
            hash_function=hash_function
        )
        bloom_filter.update(*values)

        return bloom_filter

    @cached_property
    def capacity(self) -> int:
        return self._capacity

    @cached_property
    def false_positive_probability(self) -> float:
        return self._false_positive_probability

    @cached_property
    def hash_function(self):
        return self._hash_function

    @cached_property
    def _necessary_bit_size(self) -> float:
        """
        Calculate the necessary number of bits needed to fulfill the requested false positive probability rate.

        Note that the calculated number needs to be adjusted for practical use; the actual bit size must depend on the
        number of necessary _slices_, which must all be of the same size. The number of necessary slices must thus
        evenly divide the actual bit size.

        :return: The calculated number of necessary bits to maintain the false positive probability rate, as a float.
        """

        # m: num bits in data structure
        # n: requested capacity
        # P: requested false positive probability
        # m = n * (-log2(P) / ln(2))

        return self.capacity * (-log(self._false_positive_probability, 2) / log(2))

    @cached_property
    def num_slices(self) -> int:
        return ceil(-log(self.false_positive_probability, 2))

    @cached_property
    def num_bits_per_slice(self) -> int:
        return ceil(self._necessary_bit_size / self.num_slices)

    @cached_property
    def bit_size(self):
        return self.num_slices * self.num_bits_per_slice

    def __contains__(self, value) -> bool:
        return all(
            self._bit_array[slice_index * self.num_bits_per_slice + hash_value]
            for slice_index, hash_value in enumerate(self._hash(bytes(value)))
        )

    def __len__(self) -> int:
        return self._num_elements_mapped

    def __bytes__(self) -> bytes:
        return self._bit_array.tobytes()

    def export_bytes(self) -> bytes:
        """
        Export a `BloomFilter` instance as a byte sequence.

        The hash function is a complication; it is exported as a name byte string.

        :return: A byte sequence representation of a `BloomFilter` instance.
        """

        capacity_bytes: bytes = struct_pack('>Q', self._capacity)
        false_positive_probability_bytes: bytes = struct_pack('f', self._false_positive_probability)
        hash_function_name_bytes: bytes = self.hash_function.__name__.encode()

        bit_array_bytes: bytes = self._bit_array.tobytes()

        return b''.join([
            capacity_bytes,
            false_positive_probability_bytes,
            struct_pack(self._IMPORT_EXPORT_LENGTH_FORMAT, len(hash_function_name_bytes)),
            hash_function_name_bytes,
            struct_pack(self._IMPORT_EXPORT_LENGTH_FORMAT, len(bit_array_bytes)),
            bit_array_bytes
        ])

    @classmethod
    def import_bytes(cls, data: bytes, hash_function=None, base_offset: int = 0) -> BloomFilter:
        """
        Import an exported `BloomFilter` byte sequence and make an instance.

        :param data: A byte sequence from which to extract the data representing a `BloomFilter`.
        :param hash_function: A hash function to use in case the exported name cannot be looked up in the `hashlib`.
            module.
        :param base_offset: The offset from the start of the byte sequence from where to start extracting.
        :return: A `BloomFilter` instance as represented by the pointed-to byte sequence.
        """

        offset = base_offset

        capacity = struct_unpack_from('>Q', buffer=data, offset=offset)[0]
        offset += struct_calcsize('>Q')

        false_positive_probability = struct_unpack_from('f', buffer=data, offset=offset)[0]
        offset += struct_calcsize('f')

        hash_function_name_bytes_len: int = struct_unpack_from(cls._IMPORT_EXPORT_LENGTH_FORMAT, buffer=data, offset=offset)[0]
        offset += struct_calcsize(cls._IMPORT_EXPORT_LENGTH_FORMAT)
        hash_function_name: str = data[offset:offset+hash_function_name_bytes_len].decode()
        offset += hash_function_name_bytes_len

        bit_array_bytes_len: int = struct_unpack_from(cls._IMPORT_EXPORT_LENGTH_FORMAT, buffer=data, offset=offset)[0]
        offset += struct_calcsize(cls._IMPORT_EXPORT_LENGTH_FORMAT)

        bit_array = bitarray()
        bit_array.frombytes(data[offset:offset + bit_array_bytes_len])

        return cls(
            capacity=capacity,
            false_positive_probability=false_positive_probability,
            hash_function=hash_function or getattr(hashlib, hash_function_name),
            bit_array=bit_array
        )

    def add(self, value: SupportsBytes) -> bool:
        """
        Add a value to the Bloom filter.

        :param value: The value to be added to the Bloom filter.
        :return: Whether a value was already mapped to the same bits as the provided value's.
        """

        if self._num_elements_mapped > self.capacity:
            raise IndexError('The Bloom filter is at capacity. The requested false positive rate cannot be fulfilled.')

        bit_statuses: List[bool] = []

        for slice_index, slice_bit_index in enumerate(self._hash(bytes(value))):
            bit_index: int = slice_index * self.num_bits_per_slice + slice_bit_index
            bit_statuses.append(self._bit_array[bit_index])
            self._bit_array[bit_index] = True

        self._num_elements_mapped += 1

        return all(bit_statuses)

    def update(self, *values: SupportsBytes) -> Tuple[bool, ...]:
        """
        Add multiple values to the Bloom filter.

        :param values: The values to be added to the Bloom filter.
        :return: A tuple of booleans indicating whether each of the provided values had already had their bits set.
        """

        return tuple(self.add(value=value) for value in values)
