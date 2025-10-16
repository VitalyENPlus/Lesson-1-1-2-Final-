def is_monotonic(nums):
    if len(nums) <= 1:
        return True
    
    increasing = True
    decreasing = True
    
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            decreasing = False
        elif nums[i] < nums[i - 1]:
            increasing = False
    
    return increasing or decreasing


if __name__ == "__main__":
    nums1 = [1, 2, 2, 3]
    print(f"Input: nums = {nums1}")
    print(f"Output: {is_monotonic(nums1)}")
    print()
    
    nums2 = [6, 5, 4, 4]
    print(f"Input: nums = {nums2}")
    print(f"Output: {is_monotonic(nums2)}")
    print()
    
    nums3 = [1, 3, 2]
    print(f"Input: nums = {nums3}")
    print(f"Output: {is_monotonic(nums3)}")
    print()
    
    print("Additional tests:")
    print(f"[1, 1, 1] -> {is_monotonic([1, 1, 1])}")
    print(f"[5] -> {is_monotonic([5])}")
    print(f"[] -> {is_monotonic([])}")
    print(f"[1, 2, 3, 4, 5] -> {is_monotonic([1, 2, 3, 4, 5])}")
    print(f"[5, 4, 3, 2, 1] -> {is_monotonic([5, 4, 3, 2, 1])}")
    print(f"[1, 5, 3, 7] -> {is_monotonic([1, 5, 3, 7])}")
