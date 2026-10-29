# Лабораторна робота №3: Веб-API "Облік завантаження каналів зв'язку"

Cервіс обліку вимірювань завантаження каналів.

---

### Завантаження залежностей

залежності були завантажені за допомогою devenv
```nix
package = pkgs.python314.withPackages (ps: with ps; [
  fastapi
  uvicorn
  pydantic
  ruff
]);
```
Для активаці devenv потрібно ввести:
```bash
❯ devenv shell
```

Але також як додатковий варіант я прописав залежності в requirements.txt

### Користування

База даних заповнюється за допомогою команди:
```bash
❯ python -m labs.lab3.seed
```
Запустити API можна за допомогою:
```bash
❯ uvicorn labs.lab3.main:app --reload
```