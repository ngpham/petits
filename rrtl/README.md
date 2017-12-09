#### Restricted Real-Time Logic verification

An implementation following [Jahanian and Mok] paper: Graph-Theoretic Approach for Timing Analysis
and its Implementation.

Problem: Having a system designed with System Properties, we need to assert its safety.
A design is valid if:
- forall x,y,...: SP(x,y,...) -> SF(x,y,...) is valid (true with all x,y,...)
- Equivalently: (SP /\ not SF) is unsatisfiable (false with all x,y,...)
- F = (SP /\ not SF) is written as a CNF formula (the input).
- Answer: F is unsatisfiable (the given design is valid). Or: F is satisfiable (the design is invalid).

#### Dependencies
pyparsing
