n = int(input())
num = list(map(int, input().split()))

if all(x >= 0 for x in num):
    print("Yes")
else:
    print("No")