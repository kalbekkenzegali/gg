n = int(input())
num = list(map(int, input().split()))

def square(a):
    return a**2

print(sum(map(square, num)))