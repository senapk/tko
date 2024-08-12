{ pkgs }: {
    deps = [
        pkgs.graphviz
        pkgs.python3
        pkgs.nodejs-18_x
        pkgs.nodePackages.typescript-language-server
        pkgs.yarn
        pkgs.replitPackages.jest
    ];
}
