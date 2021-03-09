window.onload = function()
{
	let current_date = new Date();
	let local_utc = -current_date.getTimezoneOffset()/60;
	document.getElementById('user-timezone').value = String(local_utc);
}