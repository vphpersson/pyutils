# Heavily inspired by python-bloomfilter.

from hashlib import sha3_256
from struct import pack, Struct
from math import ceil, log
from functools import cached_property
from collections.abc import Sized, Container
from typing import SupportsBytes, Callable, Generator

from bitarray import bitarray


class _IndexNumberStruct(Struct):

    def __init__(self, num_slice_bits: int):
        """
        Initialize a `Struct` to be used for unpacking index numbers from a hash.

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
    hash_function=sha3_256
) -> Callable[[bytes], Generator[int, None, None]]:
    """
    Make a customized aggregated hash function that yields index numbers into Bloom filter slices.

    The necessary size of the index number type are chosen based on the input parameters.

    :param num_slices: The number of slices that the Bloom filter uses.
    :param num_bits_per_slice: The number of bits in each of the slices that the Bloom filter uses.
    :param hash_function: The underlying hash function to be used.
    :return: A customized aggregated hash function.
    """

    # Choose the smallest struct type that can index all slots in a slice.
    # NOTE: The chosen struct type is very possibly able to store larger numbers than the number of bits per slice. To
    # take that into account, unpacked numbers are transformed with the modulo operator. If the number of bits per slice
    # does not evenly divide the maximum struct type value, the distribution will not be truly uniform.
    slice_index_number_struct: Struct = _IndexNumberStruct(num_slice_bits=num_bits_per_slice)

    # The struct type size may not evenly divide the resulting hash size; determine the number of index numbers that
    # fit into the hash.
    num_slice_index_numbers_in_hash = hash_function().digest_size // slice_index_number_struct.size

    # Use as many hash functions as are necessary to assure that each slice is indexed. Each hash function must be
    # salted as to make them independent.
    num_different_hash_functions = ceil(num_slices / num_slice_index_numbers_in_hash)
    salt_values = tuple(pack('I', i) for i in range(num_different_hash_functions))

    def aggregated_hash_function(value: bytes):

        num_slice_indices_provided = 0

        for salt_value in salt_values:
            hash_value: bytes = hash_function(salt_value + value).digest()

            for hash_offset_index in range(num_slice_index_numbers_in_hash):
                yield slice_index_number_struct.unpack_from(
                    buffer=hash_value,
                    offset=hash_offset_index * slice_index_number_struct.size
                )[0] % num_bits_per_slice

                num_slice_indices_provided += 1
                if num_slice_indices_provided == num_slices:
                    return

    return aggregated_hash_function


class BloomFilter(Sized, Container):

    def __init__(
        self,
        capacity: int,
        false_positive_probability: float = 0.001,
        hash_function=sha3_256
    ):
        """
        The bit size of the Bloom filter is calculated based on the requested capacity and false positive probability
        rate.

        The provided hash function will be salted in order to simulate different hash functions.

        :param capacity: The maximum number of elements to be mapped.
        :param false_positive_probability: The accepted false positive probability rate.
        :param hash_function: The underlying hash function to be used.
        """

        self._false_positive_probability = false_positive_probability
        self._capacity = capacity
        self._num_elements_mapped = 0

        self._hash: Callable[[bytes], Generator[int, None, None]] = _make_aggregated_hash_function(
            num_slices=self.num_slices,
            num_bits_per_slice=self.num_bits_per_slice,
            hash_function=hash_function
        )

        self._bit_array = bitarray(self.bit_size)
        self._bit_array.setall(False)

    @cached_property
    def capacity(self) -> int:
        return self._capacity

    @cached_property
    def false_positive_probability(self) -> float:
        return self._false_positive_probability

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

    def add(self, value: SupportsBytes):
        if self._num_elements_mapped > self.capacity:
            raise IndexError("The Bloom filter is at capacity. The requested false positive rate cannot be fulfilled.")

        for slice_index, hash_value in enumerate(self._hash(bytes(value))):
            self._bit_array[slice_index * self.num_bits_per_slice + hash_value] = True

        self._num_elements_mapped += 1
