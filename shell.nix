{ pkgs ? import <nixpkgs> { system = builtins.currentSystem; }
, lib ? pkgs.lib
, cmake ? pkgs.cmake
, pkg-config ? pkgs.pkg-config
, util-linux ? pkgs.util-linux
, hexdump ? pkgs.hexdump
, boost ? pkgs.boost
, libevent ? pkgs.libevent
, miniupnpc ? pkgs.miniupnpc
, zeromq ? pkgs.zeromq
, zlib ? pkgs.zlib
, db48 ? pkgs.db48
, sqlite ? pkgs.sqlite
, qrencode ? pkgs.qrencode
, python3 ? pkgs.python3
}:

pkgs.mkShell {
  nativeBuildInputs = [ cmake pkg-config ]
    ++ lib.optionals pkgs.stdenv.isLinux [ util-linux ];

  buildInputs = [ boost libevent db48 sqlite miniupnpc zeromq zlib python3 ];

  # Environment setup
  shellHook = ''
    export CMAKE_FLAGS="-DCMAKE_BUILD_TYPE=Release -DENABLE_WALLET=ON -DBUILD_TESTS=OFF -DSECP256K1_BUILD_TESTS=OFF -DWITH_SV2=ON"
  '';
}
