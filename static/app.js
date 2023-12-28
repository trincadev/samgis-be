const jsonBtn = document.getElementById("getJson");
const apiBtn = document.getElementById("getApi");
const output = document.getElementById("output");
const coordsForm = document.getElementById("coords-form");

function formData2json(dataId, newObj={}) {
    const formData = new FormData(dataId);
    formData.forEach(function(value, key){
        console.log(`formData2json:: key=${key}, value=${value}.`)
        newObj[key] = value;
    });
    return JSON.stringify(newObj);
}

coordsForm.addEventListener('submit', event => {
    event.preventDefault();
    console.log("coordsForm::", coordsForm, "#")
    const inputJson = formData2json(coordsForm)
    console.log("inputJson", inputJson, "#");

    fetch('/infer_samgis', {
        method: 'POST', // or 'PUT'
        body: inputJson,  // a FormData will automatically set the 'Content-Type',
        headers: {"Content-Type": "application/json"},
    }).then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log("data:", data, "#")
        output.innerHTML = JSON.stringify(data)
    }).catch(function (err) {
        console.log("err:", err, "#")
        output.innerHTML = `err:${JSON.stringify(err)}.`;
    });
    event.preventDefault();
});
