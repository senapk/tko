{ pkgs }: {
    deps = [
        pkgs.graphviz
        pkgs.python3
        pkgs.graalvm17-ce
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
    ];
}
