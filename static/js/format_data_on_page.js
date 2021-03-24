window.onload = function()
{
  date_format_on_page("iso-data");
  number_format_on_page("number-format");
}
    
function setDatesToElements(ids)
{
  for (let i=0; i<ids.length; i++) {
    let elem_date = document.getElementById(ids[i]);
    let date = new Date(elem_date.innerHTML);
    elem_date.innerHTML = formatDate(date);
  }
}

//ищет все элементы класса и меняет дату на локальную
function date_format_on_page(class_name)
{
  let elements = document.getElementsByClassName(class_name);
  for (let i=0; i<elements.length; i++) {
    elements[i].innerHTML = formatDate(new Date(elements[i].innerHTML));
  }
}

//дата в стандарте Ecma 402
function formatDate(date)
{
  let options = {
    year: 'numeric',
    month: 'numeric', //long
    day: 'numeric',
    timezone: 'UTC',
    hour: 'numeric',
    minute: 'numeric'
  };
  return date.toLocaleString('ru', options);
}

function number_format_on_page(class_name) {
  let elements = document.getElementsByClassName(class_name);
    for (let i=0; i<elements.length; i++) {
      elements[i].innerHTML = number_format(elements[i].innerHTML, 2, ',', ' ');
    }
}
// type_num - тип возвращаемого числа
function str_to_number(str_num, type_num)
{
  if (!str_num) {
    return 0;
  }

  if (type_num == undefined) {
    type_num = 'float';
  }

  if (type_num == 'float') {
    return parseFloat(str_num.replace(/\s/g, '').replace(',', '.'));
  }
  else if (type_num == 'int') {
    return parseInt(str_num.replace(/\s/g, ''));
  }
  else {
    return 0;
  }
}
/***
number - исходное число
decimals - количество знаков после разделителя
dec_point - символ разделителя
thousands_sep - разделитель тысячных
***/
function number_format(number, decimals, dec_point, thousands_sep) {
  number = (number + '').replace(/[^0-9+\-Ee.]/g, '');
  let n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      let k = Math.pow(10, prec);
      return '' + (Math.round(n * k) / k).toFixed(prec);
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n))
    .split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '')
    .length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1)
      .join('0');
  }
  return s.join(dec);
}
//  Пример 1: number_format(1234.56);
//  Результат: '1,235'
 
//  Пример 2: number_format(1234.56, 2, ',', ' ');
//  Результат: '1 234,56'
 
//  Пример 3: number_format(1234.5678, 2, '.', '');
//  Результат: '1234.57'
 
//  Пример 4: number_format(67, 2, ',', '.');
//  Результат: '67,00'
 
//  Пример 5: number_format(1000);
//  Результат: '1,000'
 
//  Пример 6: number_format(67.311, 2);
//  Результат: '67.31'
 
//  Пример 7: number_format(1000.55, 1);
//  Результат: '1,000.6'
 
//  Пример 8: number_format(67000, 5, ',', '.');
//  Результат: '67.000,00000'
 
//  Пример 9: number_format(0.9, 0);
//  Результат: '1'
 
//  Пример 10: number_format('1.20', 2);
//  Результат: '1.20'
 
//  Пример 11: number_format('1.20', 4);
//  Результат: '1.2000'
 
//  Пример 12: number_format('1.2000', 3);
//  Результат: '1.200'
 
//  Пример 13: number_format('1 000,50', 2, '.', ' ');
//  Результат: '100 050.00'
 
//  Пример 14: number_format(1e-8, 8, '.', '');
//  Результат: '0.00000001'