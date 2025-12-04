# liboqs deployment (Dec 2025)

- Host (85.239.243.227): /tmp/liboqs.zip (built Dec 3, 2025)
- pct 201: installed at /usr/local/lib/liboqs.so.0.15.0 (also .so.9, .a, pkgconfig/CMake)
- pct 200: installed Dec 4, 2025 from /home/setup/liboqs.zip
- Install steps (pct 200):
  - sudo apt-get update && sudo apt-get install -y unzip pkg-config
  - sudo unzip -o /home/setup/liboqs.zip -d /
  - sudo ldconfig
- Verify: ls /usr/local/lib/liboqs* ; pkg-config --modversion liboqs (0.10.1)
