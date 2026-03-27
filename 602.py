n = int(input())
num = list(map(int, input().split()))

def even(a):
    return a % 2 == 0

print(len(list(filter(even, num))))