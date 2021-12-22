function createClickRateOverTime() {
  var ctx = document.getElementById("click-rate-over-time").getContext("2d");
  var currentCycle = JSON.parse(
    document.getElementById("currentCycle").innerText
  );
  var previousCycles = JSON.parse(
    document.getElementById("previousCycles").innerText
  );

  var labels = ["Low (1, 2)", "Moderate (3, 4)", "High (5, 6)"];
  var datasets = [
    {
      data: [
        Math.round(currentCycle.stats.stats.low.clicked.ratio * 100),
        Math.round(currentCycle.stats.stats.moderate.clicked.ratio * 100),
        Math.round(currentCycle.stats.stats.high.clicked.ratio * 100),
      ],
      label: `Report Cycle`,
      backgroundColor: "#064875",
    },
  ];

  var colors = ["#fcbf10", "#007bc1"];

  if (previousCycles.length > 0) {
    for (var i = 0; i <= previousCycles.length; i++) {
      if (i < 2) {
        datasets.push({
          data: [
            Math.round(previousCycles[i].stats.stats.low.clicked.ratio * 100),
            Math.round(
              previousCycles[i].stats.stats.moderate.clicked.ratio * 100
            ),
            Math.round(previousCycles[i].stats.stats.high.clicked.ratio * 100),
          ],
          label: `Cycle #${i + 2}`,
          backgroundColor: colors[i],
        });
      }
    }
  }

  const data = {
    labels: labels,
    datasets: datasets.reverse(),
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: "right",
      },
      datalabels: {
        color: "white",
        font: {
          weight: "bold",
        },
        display: function (context) {
          return context.dataset.data[context.dataIndex] > 0;
        },
        formatter: function (value, ctx) {
          return value + "%";
        },
      },
    },
    scales: {
      y: {
        ticks: {
          maxTicksLimit: 4,
        },
      },
    },
  };

  const chart = new Chart(ctx, {
    type: "bar",
    data: data,
    options: options,
    plugins: [ChartDataLabels],
  });
}
