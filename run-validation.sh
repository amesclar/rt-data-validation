# ussage:
# ./run-validation.sh test_data_samples/135-fw.xml test_data_samples/135-rt.xml
#
# ./run-validation.sh test_data/1235-fw.xml test_data/1235-rt.xml
#
clear;

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Expected or Actual results file is missing. BOTH must be provided"
  exit 1
else
  FW_XML=$1
  RT_XML=$2
fi

if head -n 1 "$FW_XML" | grep -q "xml"; then
  echo "$FW_XML >>> 'xml' found in 1st line - header update not required"
else
  echo "adding xml header info"
  sed -i '1i# <?xml version="1.0" encoding="UTF-8"?><Tests>' $RT_XML
  echo "</Tests>" >> $FW_XML
fi

if head -n 1 "$RT_XML" | grep -q "xml"; then
  echo "$RT_XML >>> 'xml' found in 1st line - header update not required"
else
  echo "adding xml header info"
  sed -i '1i# <?xml version="1.0" encoding="UTF-8"?><events>' $RT_XML
  echo "</events>" >> $RT_XML
fi


python data-validation-ai-python.py --expected "$FW_XML" --actual "$RT_XML" --df --junit test-results.xml
# python data-validation-ai-python.py --expected "$FW_XML" --actual "$RT_XML" --df  > cfa.txt ; egrep FAIL cfa.txt
