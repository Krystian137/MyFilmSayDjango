document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.reply-comment').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const replyForm = this.nextElementSibling;
            replyForm.style.display = (replyForm.style.display === 'none' || replyForm.style.display === '') ? 'block' : 'none';
        });
    });
});

setTimeout(function() {
    var flashMessages = document.querySelectorAll('.flash-messages .alert');
    console.log('Flash messages:', flashMessages);
    flashMessages.forEach(function(message) {
        message.style.transition = "opacity 1s ease";
        message.style.opacity = 0;
        setTimeout(function() {
            message.remove();
        }, 1000);
    });
}, 5000);

document.querySelectorAll('.delete-comment').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const commentId = this.dataset.commentId;

        fetch(`/delete_comment/${commentId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentElement = document.getElementById(`comment-${commentId}`);
                if (commentElement) {
                    commentElement.remove();
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

document.querySelectorAll('.delete-reply').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const replyId = this.dataset.replyId;

        fetch(`/delete_reply/${replyId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const replyElement = document.querySelector(`[data-reply-id="${replyId}"]`);
                if (replyElement) {
                    replyElement.remove();
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

var closeButtons = document.querySelectorAll('.flash-messages .close');
console.log('Close buttons:', closeButtons);
closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
        var alert = this.parentElement;
        alert.style.transition = "opacity 1s ease";
        alert.style.opacity = 0;
        setTimeout(function() {
            alert.remove();
        }, 1000);
    });
});

document.querySelectorAll('.vote-button').forEach(button => {
    button.addEventListener('click', function () {
        const commentId = this.dataset.commentId;
        const voteType = this.dataset.voteType;

        fetch('/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comment_id: commentId,
                vote_type: voteType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentElement = this.closest('.comment, .reply');
                const likeButton = commentElement.querySelector(`.vote-button[data-comment-id="${commentId}"][data-vote-type="like"]`);
                const dislikeButton = commentElement.querySelector(`.vote-button[data-comment-id="${commentId}"][data-vote-type="dislike"]`);

                if (likeButton) likeButton.innerHTML = `Like (${data.likes})`;
                if (dislikeButton) dislikeButton.innerHTML = `Dislike (${data.dislikes})`;
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeScrollListener();
        initializeProgressCircles();
        initializeSortMenu();
    } catch (error) {
        console.error('Error initializing app:', error);
    }
});

function initializeScrollListener() {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;

    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;

        if (currentTop < scrollPos) {
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                console.log('Scrolling up, showing nav');
                mainNav.classList.add('is-visible');
            } else {
                console.log('Scrolling down, hiding nav');
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            mainNav.classList.remove('is-visible');
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
}

function initializeProgressCircles() {
    const circles = document.querySelectorAll('.progress-circle');
    circles.forEach(circle => {
        const percentage = circle.dataset.percentage;
        const progress = circle.querySelector('.progress-circle__progress');
        const radius = 15.9155;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (percentage / 100 * circumference);

        progress.style.strokeDasharray = `${circumference} ${circumference}`;
        progress.style.strokeDashoffset = offset;
    });
}

function initializeSortMenu() {
    const sortButton = document.getElementById('sortButton');
    const sortMenu = document.getElementById('sortMenu');

    if (sortButton && sortMenu) {
        sortButton.addEventListener('click', function() {
            sortMenu.style.display = sortMenu.style.display === 'none' || sortMenu.style.display === '' ? 'block' : 'none';
        });

        document.addEventListener('click', function(event) {
            if (!sortButton.contains(event.target) && !sortMenu.contains(event.target)) {
                sortMenu.style.display = 'none';
            }
        });
    }
}



