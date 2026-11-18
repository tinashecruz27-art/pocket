// 1. Auto-filter: submit the filter form as soon as a category is picked
const filterSelect = document.querySelector(".filter select");

filterSelect.addEventListener("change", function () {
    filterSelect.form.submit();
});


// 2. Doughnut chart of spending by category
const canvas = document.getElementById("categoryChart");

if (chartValues.length > 0) {
    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: chartLabels,
            datasets: [{
                data: chartValues,
                backgroundColor: ["#2b59c3", "#f2a541", "#3bb273", "#e15554", "#7768ae", "#4d9de0"],
            }],
        },
        options: {
            plugins: {
                legend: { position: "bottom" },
            },
        },
    });
}

console.log("Pocket JavaScript loaded!", chartLabels, chartValues);