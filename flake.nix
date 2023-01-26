{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    devshell.url = "github:numtide/devshell";
    personal = {
      url = "git+ssh://git@git.sr.ht/~showyourcode/flakes";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        flake-utils.follows = "flake-utils";
      };
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = with inputs; [
            devshell.overlay
            personal.overlay
            poetry2nix.overlay
          ];
        };
        python-env = pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          python = pkgs.python39;
        };
        rEnv = pkgs.rWrapper.override {
          packages = with pkgs.rPackages; [
            tidyverse
          ];
        };
      in
      {
        devShell = pkgs.devshell.mkShell {
          name = "test-missing-rfam-hits-shell";
          motd = "";

          packages = with pkgs; [
            jdk11
            easel
            infernal
            nextflow
            nodePackages.pyright
            poetry
            python-env
            rEnv
            wget
          ];
        };
      }
    );
}
