window.onload = function()
{
    date_format("iso-data");
}
//устанавливает форматированные локальные даты в каждый эелемент из массива id
function setDatesToElements(ids)
{
	for (let i=0; i<ids.length; i++) {
            let elem_date = document.getElementById(ids[i]);
            let date = new Date(elem_date.innerHTML);
            elem_date.innerHTML = formatDate(date);
	}
}
//ищет все элементы класса и меняет дату на локальную
function date_format(class_name)
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