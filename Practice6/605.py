s = input()

vowels = "aeiouAEIOU"
if any(a in vowels for a in s):
    print("Yes")
else:
    print("No")