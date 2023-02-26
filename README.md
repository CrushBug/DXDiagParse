# DXDiagParse
DXDiagParse is a Python script that parses a DXDiag report text file and summerizes the common details for easier reading.

DXDiagParse only needs the os and sys Python libraries.

DXDiagParse translates raw AMD and NVIDIA driver versions into human readable versions where is can. For example, it will turn an AMD "31.00.12029.10015 (English)" into "Adrenalin 22.11.2 Recommended (WHQL)" and an NVIDIA "31.00.0015.2661 (English)" into "526.61".

## Command Line
```
parsedxdiag.py [DXDiag.txt]
```

## Sample
Here is a sample report summary.
```
DxDiag Report Parser 1.11
-------------------------
Report time:      4/20/2022, 00:00:00
Computer Name:    DESKTOP-Sample
OS:               Windows 11 Home 64-bit (10.0, Build 22000) (22000.co_release.210604-1628)
Language:         English (Regional Setting: English)
System:           Micro-Star International
CPU:              AMD Ryzen 7 4800H with Radeon Graphics (16 CPUs), ~2.9GHz
RAM:              16 GB
Page File:        9733MB used, 14741MB available
DirectX:          DirectX 12

Video display 1
Video card:       NVIDIA GeForce RTX 3080
Driver version:   526.61
VRAM:             10 GB
Display mode:     2560 x 1440 (32 bit) (144Hz)
Monitor name:     Dell S2716DG(DisplayPort)

Video display 2
Video card:       NVIDIA GeForce RTX 3080
Driver version:   526.61
VRAM:             10 GB
Display mode:     1920 x 1200 (32 bit) (59Hz)
Monitor name:     SyncMaster 245T(Digital)

Video display 3
Video card:       NVIDIA GeForce RTX 3080
Driver version:   526.61
VRAM:             10 GB
Display mode:     1920 x 1080 (32 bit) (60Hz)
Monitor name:     BenQ GW2255

Sound devices:    Headphones (Arctis 5 Game)
                  Headset Earphone (Arctis 5 Chat)

Drives:           C D
Drive info:       C: (free 32.6 GB/102.0 GB) NTFS - Samsung SSD 850 EVO 500GB
                  D: (free 90.0 GB/374.4 GB) NTFS - Samsung SSD 850 EVO 500GB
```
