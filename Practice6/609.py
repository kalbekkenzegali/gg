n = int(input())
keys = input().split()
values = input().split()

d = dict(zip(keys, values))

a = input()

if a in d:
    print(d[a])
else: 
    print("Not found")