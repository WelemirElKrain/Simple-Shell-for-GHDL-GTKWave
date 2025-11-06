# Simple Shell for GHDL GTKWave
Lightweight PyQt5 interface for running VHDL simulations using GHDL and viewing waveforms in GTKWave.  
Designed for students and lab work.

## Requirements
- Python 3.8+
- PyQt5 (`pip install PyQt5`)
- GHDL (https://github.com/ghdl/ghdl/releases)
- GTKWave (http://gtkwave.sourceforge.net/)

## Usage
1. Run `main.py`
2. In menu → **Set PATH**, specify paths to:
   - `ghdl.exe` (e.g. `C:\ghdl\bin\ghdl.exe`)
   - `gtkwave.exe` (e.g. `C:\gtkwave\bin\gtkwave.exe`)
3. Open your `.vhdl` or `.vhd` files
4. First press **Test** for each file (syntax + dependency check)
5. Then open the **testbench** file and press **Compile & Run**
6. When simulation finishes, click **Run GTKWave** to open `wave.vcd`

## Example
A working example is in the `examples/` folder:
```
examples/
├── and_gate.vhdl
└── testbench.vhdl
```
To test:
- Open `and_gate.vhdl`
- Click **Test**
- Open `testbench.vhdl`
- Click **Test**
- Then **Compile & Run**
- View results in GTKWave

## License
MIT License — free for educational and research use.
