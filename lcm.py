def lcm_calc(n1, n2):
    if n1 > n2:
        greater = n1
    else:
        greater = n2
    while True:
        if (greater % n1 == 0) and (greater % n2 == 0):
            lcm = greater
            break
        greater += 1
    return lcm
a = int(input('Enter a:'))
b = int(input('Enter b:'))
lcm_a_b = lcm_calc(a, b)
print('LCM(', a, ',', b, ') = ', lcm_a_b)


