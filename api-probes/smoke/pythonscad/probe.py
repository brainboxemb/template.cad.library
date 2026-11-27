"""API-probe infrastructure smoke: one small standalone solid."""
from pythonscad import cube

model = cube([12, 8, 4], center=True).up(2)
