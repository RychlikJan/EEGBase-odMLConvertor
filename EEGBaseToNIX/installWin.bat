IF EXIST "convert.py" (
  echo "convert.py exist"
) ELSE (
  exit
)

IF EXIST "mnetonix.py" (
  echo "mnetonix.py exist"
) ELSE (
  exit
)
pip install -r requirements.txt