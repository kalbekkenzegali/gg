n = int(input())
a = input().split()

print(" ".join(f'{i}:{w}' for i, w in enumerate(a)) )