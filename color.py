class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g 
        self.b = b

    def step(self, steps):
        self.r = self.r - steps["r"]
        self.g = self.g - steps["g"]
        self.b = self.b - steps["b"]
    
    def rgb_to_hex(self):
        return f"#{int(self.r):02X}{int(self.g):02X}{int(self.b):02X}"

    def __str__(self):
        return f"{self.r} {self.g} {self.b}"
    