document.addEventListener("DOMContentLoaded", () => {
    const chartCanvas = document.getElementById(
        "categoryValuationChart"
    );

    if (!chartCanvas) {
        return;
    }

    const chartDataElement = document.getElementById(
        "categoryValuationData"
    );

    if (!chartDataElement) {
        return;
    }

    const categoryValuations = JSON.parse(
        chartDataElement.textContent
    );

    const categories = Object.keys(categoryValuations);
    const inventoryValues = Object.values(categoryValuations);

    new Chart(chartCanvas, {
        type: "bar",

        data: {
            labels: categories,
            datasets: [
                {
                    label: "Inventory Value (₦)",
                    data: inventoryValues,
                },
            ],
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            scales: {
                y: {
                    beginAtZero: true,
                },
            },

            plugins: {
                legend: {
                    display: false,
                },

                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const value = context.raw;

                            return `₦${value.toLocaleString()}`;
                        },
                    },
                },
            },
        },
    });
});