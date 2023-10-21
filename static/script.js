const coordsGenForm = document.querySelector(".coords-gen-form");

const segmentCoords = async (coords) => {
  const inferResponse = await fetch(`infer_samgeo?input=${coords}`);
  const inferJson = await inferResponse.json();

  return inferJson.output;
};

coordsGenForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const coordsGenInput = document.getElementById("coords-gen-input");
  const coordsGenParagraph = document.querySelector(".coords-gen-output");

  coordsGenParagraph.coordsContent = await segmentCoords(coordsGenInput.value);
});