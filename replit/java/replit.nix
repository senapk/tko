{ pkgs }: {
    deps = [
        pkgs.python38Full
        pkgs.python38Packages.appdirs
        pkgs.graalvm17-ce
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
    ];
}
