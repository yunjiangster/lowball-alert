{ pkgs, ... }: {
  channel = "stable-24.05";

  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
  ];

  idx = {
    extensions = [ "ms-python.python" ];
    workspace = {
      # This ensures that EVERY time you open a terminal, it's ready.
      onStart = {
        activate-venv = ''
          if [ ! -d ".venv" ]; then
            python3 -m venv .venv
          fi
          source .venv/bin/activate
          # Quick check for updates
          pip install --upgrade yfinance > /dev/null 2>&1
        '';
      };
    };
  };
}