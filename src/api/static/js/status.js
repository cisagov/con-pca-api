function createDoughnut(chartId, subtotal, total) {
  var ctx = document.getElementById(chartId).getContext("2d");
  const data = {
    datasets: [
      {
        data: [subtotal, total - subtotal],
        backgroundColor: ["#0078ae", "#cecece"],
        borderWidth: 0,
        cutout: "65%",
        datalabels: {
          anchor: "end",
        },
      },
    ],
  };

  const options = {
    animation: false,
    plugins: {
      datalabels: {
        backgroundColor: function (context) {
          return context.dataset.backgroundColor;
        },
        borderColor: "white",
        borderRadius: 25,
        borderWidth: 2,
        color: "white",
        display: function (context) {
          var dataset = context.dataset;
          var value = dataset.data[context.dataIndex];
          return value > 0;
        },
        font: {
          weight: "bold",
        },
        padding: 6,
      },
    },
    // Core options
    aspectRatio: 1,
    layout: {
      padding: 15,
    },
  };

  const chart = new Chart(ctx, {
    type: "doughnut",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
  chart.canvas.parentNode.style.width = "160px";
}

function createSparkline(chartId, allCyclesData) {
  let clickData = allCyclesData.split(", ");
  const ctx = document.getElementById(chartId).getContext("2d");
  ctx.canvas.width = 500;
  ctx.canvas.height = 50;
  let data = {
    labels: clickData,
    datasets: [
      {
        data: clickData,
        fill: false,
        pointRadius: 1,
        spanGaps: true,
        tension: 0,
      },
    ],
  };
  const chart = new Chart(ctx, {
    type: "line",
    data: data,
    options: {
      events: [],
      borderColor: "#000000",
      borderWidth: 1.5,
      responsive: false,
      plugins: {
        legend: {
          display: false,
          labels: {
            display: false,
          },
        },
        tooltips: {
          display: false,
        },
      },
      scales: {
        x: {
          display: false,
        },
        y: {
          display: false,
        },
      },
    },
  });
  chart.canvas.parentNode.style.width = "500px";
}
