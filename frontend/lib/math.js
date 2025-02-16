const EPSILON = 0.001

/* This function rounds the number to the closest integer if very close to it.
This avoids weird JS decimal calculations. */
const fix_decimal = (x) => {
    if ((x % 1) < EPSILON || (x % 1) > (1 - EPSILON))
        return Math.round(x)
    else
        return x
}

export { fix_decimal }