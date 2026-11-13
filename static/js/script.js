document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("header nav");

    if (menuButton && navigation) {
        menuButton.addEventListener("click", function () {
            navigation.classList.toggle("nav-open");

            const isOpen = navigation.classList.contains("nav-open");
            menuButton.setAttribute("aria-expanded", isOpen);
        });
    }
});
