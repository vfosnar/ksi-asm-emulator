{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "nixpkgs/nixos-24.11";
  };

  outputs =
    {
      self,
      flake-utils,
      nixpkgs,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311Full
            python311Packages.python-lsp-server
          ];
        };
      }
    );
}
