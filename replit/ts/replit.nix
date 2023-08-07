
{ pkgs }: {
    deps = [
        pkgs.python38Full
        pkgs.python38Packages.appdirs
        pkgs.yarn
        pkgs.esbuild
        pkgs.nodejs-18_x
        pkgs.nodePackages.typescript
        pkgs.nodePackages.typescript-language-server
    ];
}