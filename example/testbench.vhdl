library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity testbench is
end entity testbench;

architecture sim of testbench is
    signal A, B, Y : std_logic := '0';
begin
    uut: entity work.and_gate
        port map (
            A => A,
            B => B,
            Y => Y
        );

    process
    begin
        A <= '0'; B <= '0'; wait for 20 ns;
        A <= '0'; B <= '1'; wait for 20 ns;
        A <= '1'; B <= '0'; wait for 20 ns;
        A <= '1'; B <= '1'; wait for 20 ns;
        wait;
    end process;
end architecture sim;