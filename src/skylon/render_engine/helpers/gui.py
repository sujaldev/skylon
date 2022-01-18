def fun(start, end, lcm):
    print(f"start: {start}, end: {end}, lcm: {lcm}")
    if lcm > end:
        return 0
    elif lcm == end:
        return 1
    else:
        x = start // lcm
        y = end // lcm
        if x * lcm >= start:
            return y - x + 1
        else:
            return y - x


def fun1(lcm, list_of_primes, start, end, stage):
    sign = (-1) ** stage
    k = sign * fun(start, end, lcm)
    if len(list_of_primes) == 0:
        return k
    for x in range(len(list_of_primes)):
        k += fun1(lcm * list_of_primes[x], list_of_primes[x + 1::], start, end, stage + 1)
        print(f"list_of_primes: {list_of_primes}, k: {k}, lcm: {lcm}, stage: {stage}, start: {start}, end: {end}")
    return k


t = int(input())
for __ in range(t):
    _, range_start, range_end = [int(i) for i in input().split()]
    list_of_prime = [int(i) for i in input().split()]

    num_of_elems_in_range = range_end - range_start + 1
    k = fun1(1, list_of_prime, range_start, range_end, 1)
    print(k + num_of_elems_in_range)
