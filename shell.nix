{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.autoconf-archive
    pkgs.libtool
    pkgs.autoconf
    pkgs.automake
    pkgs.autogen
    pkgs.pkg-config
    pkgs.boost
    pkgs.libevent
    pkgs.tmux
    pkgs.sqlite
  ];
}

