library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity and_gate is
    port (
        A, B : in std_logic;
        Y    : out std_logic
    );
end entity and_gate;

architecture behavior of and_gate is
begin
    Y <= A or B;
end architecture behavior;