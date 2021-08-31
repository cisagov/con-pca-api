function createDoughnut(chartId, subtotal, total) {
  var ctx = document.getElementById(chartId).getContext("2d");
  const data = {
    datasets: [
      {
        data: [subtotal, total - subtotal],
        backgroundColor: ["#164A91", "#cecece"],
        borderWidth: 0,
        cutout: "65%",
      },
    ],
  };

  const options = {};

  new Chart(ctx, {
    type: "doughnut",
    data: data,
    options: options,
  });
}

function createStatsByLevelChart(
  chartId,
  low_sent,
  low_opened,
  low_clicked,
  mod_sent,
  mod_opened,
  mod_clicked,
  high_sent,
  high_opened,
  high_clicked
) {
  var ctx = document.getElementById(chartId).getContext("2d");
  const data = {
    labels: ["Sent", "Opened", "Clicked"],
    datasets: [
      {
        data: [low_sent, low_opened, low_clicked],
        backgroundColor: "#064875",
        label: "Low",
      },
      {
        data: [mod_sent, mod_opened, mod_clicked],
        backgroundColor: "#fcbf10",
        label: "Moderate",
      },
      {
        data: [high_sent, high_opened, high_clicked],
        backgroundColor: "#007bc1",
        label: "High",
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: "right",
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

  new Chart(ctx, {
    type: "bar",
    data: data,
    options: options,
  });
}
