{ pkgs }: {
    deps = [
        pkgs.graphviz
        pkgs.python38Full
        pkgs.graalvm17-ce
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
    ];
}
