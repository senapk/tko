{ pkgs }: {
    deps = [
        pkgs.graphviz
        pkgs.python3
        pkgs.yarn
        pkgs.esbuild
        pkgs.nodejs-18_x
        pkgs.nodePackages.typescript
        pkgs.nodePackages.typescript-language-server
    ];
}