{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    devshell.url = "github:numtide/devshell";
    personal = {
      url = "git+ssh://git@git.sr.ht/~showyourcode/flakes";
      inputs = {
        /* nixpkgs.follows = "nixpkgs"; */
        flake-utils.follows = "flake-utils";
      };
    };
  };

  outputs = inputs@{ self, nixpkgs, flake-utils, personal, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = with inputs; [
            devshell.overlay
            inputs.personal.overlay
          ];
        };
      in
      {
        devShell = pkgs.devshell.mkShell {
          name = "curation-tool-shell";
          motd = "";

          packages = with pkgs; [
            infernal
            easel
          ];
        };
      }
    );
}
