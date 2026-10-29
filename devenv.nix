{ pkgs, ... }:

{
  languages.python = {
    enable = true;
    uv.enable = true;

    package = pkgs.python314.withPackages (ps: with ps; [
      fastapi
      uvicorn
      pydantic
      ruff
    ]);
  };
}
