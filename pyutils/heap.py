from typing import Callable, Sequence, MutableSequence, Any


def _default_get_value(heap_sequence: Sequence[Any], index: int) -> Any:
    """
    Retrieve a value from the heap at an index.

    By default, the value is retrieved by an ordinary lookup at the specified index in the sequence.

    :param heap_sequence: A sequence that constitutes a heap, from which to retrieve a value.
    :param index: An index at which to retrieve a value from the heap.
    :return: The value located at the specified index in the heap.
    """

    return heap_sequence[index]


def _default_set_root(heap_sequence: MutableSequence[Any]) -> Any:
    """
    Update the root of a sequence following a request to extract the current root.

    By default, the current root is replaced by the last element in the sequence, which is moved.

    :param heap_sequence: A sequence that constitutes a heap, whose root to update.
    :return: The newly set root, or `None` in case the preceding extraction results in an empty sequence.
    """

    last_element: Any = heap_sequence.pop()

    if heap_sequence:
        heap_sequence[0] = last_element
        return last_element

    return None


def _default_swap_elements(heap_sequence: MutableSequence[Any], element_1_index: int, element_2_index: int) -> None:
    """
    Swap two elements in a heap sequence.

    :param heap_sequence: A sequence that constitutes a heap, in which the elements to be swapped are located.
    :param element_1_index: An index of one of the two elements in the sequence to be swapped.
    :param element_2_index: An index of the other one of the two elements in the sequence to be swapped.
    :return: None
    """

    heap_sequence[element_1_index], heap_sequence[element_2_index] = \
        heap_sequence[element_2_index], heap_sequence[element_1_index]


def _default_push_element(heap_sequence: MutableSequence[Any], element: Any) -> None:
    """
    Push an element to the end of a heap sequence.

    :param heap_sequence: A sequence that constitutes a heap, to which the element should be pushed.
    :param element: An element to be pushed to the heap sequence.
    :return: None
    """

    heap_sequence.append(element)


def _default_compare(
    heap_sequence: MutableSequence[Any],
    left_hand_side_index: int,
    right_hand_side_index: int,
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value
) -> bool:
    """
    Compare two elements in a heap sequence.

    By default, the comparison uses the "less than" operator, resulting in a min-heap.

    :param heap_sequence: A sequence that constitutes a heap, in which the elements to be compared are located.
    :param left_hand_side_index: An index of the element to be used on the left-hand side in the comparison.
    :param right_hand_side_index: An index of the element to be used on the right-hand side in the comparison.
    :param get_value: A function that retrieves the value located at a specified index in the heap sequence.
    :return: The boolean result of the comparison.
    """

    return get_value(heap_sequence, left_hand_side_index) < get_value(heap_sequence, right_hand_side_index)


def _heapify_down(
    heap_sequence: MutableSequence[Any],
    node_index: int,
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value,
    compare: Callable[[MutableSequence[Any], Any, Any, Callable[[MutableSequence[Any], int], Any]], bool] = _default_compare,
    swap_elements: Callable[[MutableSequence[Any], int, int], None] = _default_swap_elements
) -> None:
    """
    Establish the heap property starting from a node in a heap sequence, progressing downwards.

    :param heap_sequence: A sequence in which the node that is to have the heap property established can be located.
    :param node_index: An index to the node in the heap sequence that is to have the heap property established.
    :param get_value: A function that obtains the value at a specified index in the heap sequence.
    :param compare: A function that compares nodes in the heap sequence to determine their proper order.
    :param swap_elements: A function that swaps two elements in the heap sequence to put them at their proper location.
    :return: None
    """

    left_index = 2 * node_index + 1
    right_index = 2 * node_index + 1 + 1

    left = get_value(heap_sequence, left_index) if left_index < len(heap_sequence) else None
    right = get_value(heap_sequence, right_index) if right_index < len(heap_sequence) else None

    highest_priority_index = node_index

    if left is not None and compare(heap_sequence, left_index, highest_priority_index, get_value):
        highest_priority_index = left_index

    if right is not None and compare(heap_sequence, right_index, highest_priority_index, get_value):
        highest_priority_index = right_index

    if highest_priority_index != node_index:
        swap_elements(heap_sequence, node_index, highest_priority_index)

        _heapify_down(
            heap_sequence=heap_sequence,
            node_index=highest_priority_index,
            get_value=get_value,
            compare=compare
        )


def _heapify_up(
    heap_sequence: MutableSequence[Any],
    node_index: int,
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value,
    compare: Callable[[MutableSequence[Any], Any, Any, Callable[[MutableSequence[Any], int], Any]], bool] = _default_compare,
    swap_elements: Callable[[MutableSequence[Any], int, int], None] = _default_swap_elements
) -> None:
    """
    Establish the heap property starting from a node in a heap sequence, progressing upwards.

    :param heap_sequence: A sequence in which the node that is to have the heap property established can be located.
    :param node_index: An index to the node in the heap sequence that is to have the heap property established.
    :param get_value: A function that obtains the value at a specified index in the heap sequence.
    :param compare: A function that compares nodes in the heap sequence to determine their proper order.
    :param swap_elements: A function that swaps two elements in the heap sequence to put them at their proper location.
    :return:
    """

    current_element_index = node_index
    parent_element_index = (current_element_index - 1) // 2

    while compare(heap_sequence, current_element_index, parent_element_index, get_value) and parent_element_index >= 0:
        swap_elements(heap_sequence, current_element_index, parent_element_index)
        current_element_index = parent_element_index
        parent_element_index = (current_element_index - 1) // 2


def make_heap(
    heap_sequence: MutableSequence[Any],
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value,
    compare: Callable[[MutableSequence[Any], Any, Any, Callable[[MutableSequence[Any], int], Any]], bool] = _default_compare,
    swap_elements: Callable[[MutableSequence[Any], int, int], Any] = _default_swap_elements
) -> MutableSequence[Any]:
    """
    Mutate a sequence so that it fulfils the heap property.

    :param heap_sequence: A sequence that is to be mutated so that it fulfils the heap property.
    :param get_value: A function that obtains the value at a specified index in the heap sequence.
    :param compare: A function that compares nodes in the heap sequence to determine their proper order.
    :param swap_elements: A function that swaps two elements in the heap sequence to put them at their proper location.
    :return: None
    """

    last_node_index = len(heap_sequence) - 1
    for node_index in range((last_node_index - 1) // 2, -1, -1):
        _heapify_down(
            heap_sequence=heap_sequence,
            node_index=node_index,
            get_value=get_value,
            compare=compare,
            swap_elements=swap_elements
        )

    return heap_sequence


def heappop(
    heap_sequence: MutableSequence[Any],
    set_root: Callable[[MutableSequence[Any]], Any] = _default_set_root,
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value,
    compare: Callable[[MutableSequence[Any], Any, Any, Callable[[MutableSequence[Any], int], Any]], bool] = _default_compare,
    swap_elements: Callable[[MutableSequence[Any], int, int], Any] = _default_swap_elements
) -> Any:
    """
    Extract the root element from a heap and maintain the heap invariant.

    :param heap_sequence: A sequence that constitutes a heap, from which the root is to be extracted.
    :param set_root: A function that updates the root of the heap following the extraction of the current root.
    :param get_value: A function that obtains the value at a specified index in the heap sequence.
    :param compare: A function that compares nodes in the heap sequence to determine their proper order.
    :param swap_elements: A function that swaps two elements in the heap sequence to put them at their proper location.
    :return: The current root value of the heap.
    """

    root_element = get_value(heap_sequence, 0)
    set_root(heap_sequence)
    _heapify_down(heap_sequence=heap_sequence, node_index=0, get_value=get_value, compare=compare, swap_elements=swap_elements)

    return root_element


def heappush(
    element: Any,
    heap_sequence: MutableSequence[Any],
    push_element: Callable[[MutableSequence[Any], Any], Any] = _default_push_element,
    get_value: Callable[[MutableSequence[Any], int], Any] = _default_get_value,
    compare: Callable[[MutableSequence[Any], Any, Any, Callable[[MutableSequence[Any], int], Any]], bool] = _default_compare,
    swap_elements: Callable[[MutableSequence[Any], int, int], None] = _default_swap_elements
) -> Any:
    """
    Push an element to a heap and maintain the heap invariant.

    :param element: An element to be pushed onto the heap sequence.
    :param heap_sequence: A sequence that constitutes a heap, to which the element is to be pushed.
    :param push_element: A function that pushes the element to the heap sequence.
    :param get_value: A function that obtains the value at a specified index in the heap sequence.
    :param compare: A function that compares nodes in the heap sequence to determine their proper order.
    :param swap_elements: A function that swaps two elements in the heap sequence to put them at their proper location.
    :return: The element that is pushed to the heap sequence.
    """

    push_element(heap_sequence, element)
    _heapify_up(
        heap_sequence=heap_sequence,
        node_index=len(heap_sequence) - 1,
        get_value=get_value,
        compare=compare,
        swap_elements=swap_elements
    )

    return element
