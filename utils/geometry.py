import numpy as np

def angle_3pt(a, b, c):
    """
    Compute the angle (in degrees) formed at point b by points a–b–c.

    Steps:
      - Convert coordinates to numpy arrays.
      - Form vectors ba and bc.
      - Compute cosine of the angle using the dot product formula.
      - Clip the cosine value to the valid numeric range to avoid
        floating-point issues.
      - Convert the resulting angle from radians to degrees.
    """
    a, b, c = np.array(a), np.array(b), np.array(c)

    # Vectors from b to the outer points
    ba = a - b
    bc = c - b

    # Dot-product denominator with a small epsilon to avoid division by zero
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)

    # Cosine of the angle between vectors
    cosang = np.dot(ba, bc) / denom

    # Clamp to [-1, 1] for numerical stability
    cosang = np.clip(cosang, -1.0, 1.0)

    # Convert angle to degrees
    return np.degrees(np.arccos(cosang))


def avg(x, y):
    """
    Compute the arithmetic mean of two numeric values.
    """
    return (x + y) / 2.0
