let showAISolutionButton = null;

function submitCode() {
    const code = document.getElementById('code').value;
    const challengeMode = localStorage.getItem('challengeMode') === 'true';
    const isDailyChallenge = document.querySelector('meta[name="is-daily-challenge"]')?.content === 'true';

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            code: code,
            challengeMode: challengeMode,
            isDailyChallenge: isDailyChallenge
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            document.getElementById('result').innerText = 'Error: ' + data.error;
            return;
        }

        // Update streak counter
        updateStreakDisplay(data.streak, data.max_streak, data.streak_broken, data.passed === data.total);
        
        // Update daily streak if available
        if (data.daily_streak !== undefined && data.max_daily_streak !== undefined) {
            updateDailyStreakDisplay(data.daily_streak, data.max_daily_streak);
            
            // Show completion badge if daily challenge was completed
            if (data.daily_challenge_completed) {
                const header = document.querySelector('.daily-challenge-header');
                if (header && !document.querySelector('.completion-badge')) {
                    const badge = document.createElement('div');
                    badge.className = 'completion-badge';
                    badge.textContent = '✅ Completed Today';
                    header.appendChild(badge);
                }
            }
        }

        // Celebratory message
        let celebration = "";
        if (data.passed === data.total) {
            celebration = "<h3 style='color:green;'>🎉 All tests passed! Great job!</h3>";
            

                // Add You vs GPT-4 comparison if available
            if (data.code_comparison) {
                celebration += `
                <div class="comparison-container">
                    <h3>You vs GPT-4 Matchup</h3>
                    
                    <div class="comparison-summary ${data.code_comparison.winner === 'user' ? 'user-win' : data.code_comparison.winner === 'ai' ? 'ai-win' : 'tie'}">
                        <div class="comparison-winner">
                            ${data.code_comparison.winner === 'user' ? '🏆 You Win!' : 
                            data.code_comparison.winner === 'ai' ? '🤖 GPT-4 Wins' : '🤝 It\'s a Tie!'}
                        </div>
                        <div class="comparison-score">
                            Overall Score: ${data.code_comparison.overall_score}/100
                        </div>
                    </div>
                    
                    <div class="comparison-metrics">
                        <div class="metric">
                            <h4>Code Size</h4>
                            <div class="metric-bars">
                                <div class="metric-label">You: ${data.code_comparison.size.user_chars} chars, ${data.code_comparison.size.user_lines} lines</div>
                                <div class="metric-bar">
                                    <div class="user-bar" style="width: ${100 - data.code_comparison.size.size_score}%"></div>
                                </div>
                                <div class="metric-label">GPT-4: ${data.code_comparison.size.ai_chars} chars, ${data.code_comparison.size.ai_lines} lines</div>
                                <div class="metric-bar">
                                    <div class="ai-bar" style="width: ${data.code_comparison.size.size_score}%"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="metric">
                            <h4>Speed & Efficiency</h4>
                            <div class="metric-detail">Estimated complexity: ${data.code_comparison.speed.estimated_complexity}</div>
                            <div class="metric-bars">
                                <div class="metric-bar">
                                    <div class="user-bar" style="width: ${data.code_comparison.speed.speed_score}%"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="metric">
                            <h4>Code Elegance</h4>
                            <div class="metric-detail">Pythonic features: ${data.code_comparison.elegance.pythonic_score}/100</div>
                            <div class="metric-detail">Readability: ${data.code_comparison.elegance.readability_score}/100</div>
                            <div class="metric-bars">
                                <div class="metric-bar">
                                    <div class="user-bar" style="width: ${data.code_comparison.elegance.elegance_score}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="comparison-feedback">
                        <h4>Feedback:</h4>
                        <ul>
                            ${data.code_comparison.feedback.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                </div>`;
            }
            
            // Add reflection prompt if available
            if (data.reflection_prompt) {
                celebration += `
                <div class="reflection-box">
                    <h4>Reflect on your solution:</h4>
                    <p>${data.reflection_prompt}</p>
                    <textarea id="reflection-text" placeholder="Type your thoughts here..."></textarea>
                    <button onclick="saveReflection()" class="reflection-btn">Save Reflection</button>
                </div>`;
            }
            
            if (data.daily_challenge_completed) {
                celebration += "<h4 style='color:#ff6f00;'>🏆 You've completed today's challenge! Come back tomorrow for a new one!</h4>";
            }
        }

        // Basic stats
        let statsHTML = `
            Passed ${data.passed} out of ${data.total} tests.<br>
            Your lines: ${data.user_lines}<br>
            AI lines: ${data.ai_lines}<br>
            Attempts left: ${data.attempts_left}<br>
        `;

        // Attempt feedback
        let attemptsMessage = "";
        if (!data.move_to_next) {
            if (data.attempts_left === 2) {
                attemptsMessage = "<b>⚠️ You have 2 attempts left.</b>";
            } else if (data.attempts_left === 1) {
                attemptsMessage = "<b>⚠️ Final attempt!</b>";
            }
        }
        
        // Show hint after 2 failed attempts
        let hintHTML = "";
        if (data.show_hint && data.hint) {
            hintHTML = `
                <div class="hint-box">
                    <h4>💡 Hint:</h4>
                    <p>${data.hint}</p>
                </div>
            `;
        }

        // Show test case results with different detail levels based on mode
        let resultsHTML = `<h3>Test Results:</h3>`;
        
        // Beginner mode shows detailed feedback
        if (!challengeMode) {
            data.detailed_results.forEach((test, index) => {
                resultsHTML += `
                <div class="test-case-detail ${test.pass ? 'passed' : 'failed'}">
                    <h4>Test Case ${index + 1}: ${test.pass ? '✅ Passed' : '❌ Failed'}</h4>
                    <p><b>Input:</b> ${JSON.stringify(test.input)}</p>
                    <p><b>Expected Output:</b> ${JSON.stringify(test.expected)}</p>
                    <p><b>Your Output:</b> ${JSON.stringify(test.result)}</p>
                `;
                
                // Add detailed feedback for failed tests
                if (!test.pass) {
                    resultsHTML += `<div class="feedback-step">
                        <h4>What went wrong?</h4>`;
                    
                    // Check if it's an error message
                    if (String(test.result).includes("Error:")) {
                        resultsHTML += `<p>Your code threw an error: <code>${test.result}</code></p>`;
                    } else {
                        // Try to provide more specific feedback based on the type of mismatch
                        if (typeof test.expected !== typeof test.result) {
                            resultsHTML += `<p>Type mismatch: Expected <code>${typeof test.expected}</code> but got <code>${typeof test.result}</code></p>`;
                        } else if (Array.isArray(test.expected)) {
                            resultsHTML += `<p>Array values don't match. Check each element carefully.</p>`;
                        } else if (typeof test.expected === 'object') {
                            resultsHTML += `<p>Object values don't match. Check all keys and values.</p>`;
                        } else {
                            resultsHTML += `<p>Values don't match. Check your calculation logic.</p>`;
                        }
                    }
                    
                    if (test.hint) {
                        resultsHTML += `<p>Suggestion: ${test.hint}</p>`;
                    }
                    
                    resultsHTML += `</div>`;
                }
                
                resultsHTML += `</div>`;
            });
        } else {
            // Challenge mode shows minimal feedback
            resultsHTML += `<ul>`;
            data.detailed_results.forEach(test => {
                resultsHTML += `<li>${test.pass ? '✅' : '❌'} Test case ${test.pass ? 'passed' : 'failed'}</li>`;
            });
            resultsHTML += `</ul>`;
        }

        // Display results
        document.getElementById('result').innerHTML = `
            ${celebration}
            ${statsHTML}
            ${attemptsMessage}<br><br>
            ${hintHTML}
            ${resultsHTML}
        `;

        // Update prompt and badge if not on daily challenge
        if (!isDailyChallenge) {
            document.getElementById('prompt').innerText = data.next_question.prompt;
            const badge = document.getElementById('difficulty-badge');
            const diff = data.next_question.difficulty;
            if (diff === 1) {
                badge.textContent = "Easy";
                badge.style.backgroundColor = "green";
            } else if (diff === 2) {
                badge.textContent = "Medium";
                badge.style.backgroundColor = "orange";
            } else {
                badge.textContent = "Hard";
                badge.style.backgroundColor = "red";
            }
        }

        // Reset code area
        document.getElementById('code').value = "# Write your code here...";

        // Handle AI solution toggle (if 3 attempts used)
        if (!data.move_to_next && data.attempts_left === 3) {
            // A new question was just loaded, remove old button if present
            if (showAISolutionButton) {
                showAISolutionButton.remove();
                showAISolutionButton = null;
            }
        } else if (data.move_to_next && data.attempts_left === 3) {
            // User just failed 3 times — show AI solution button
            showAISolutionButton = document.createElement('button');
            showAISolutionButton.innerText = "💡 Show AI Solution";
            showAISolutionButton.style.marginTop = "15px";
            showAISolutionButton.onclick = () => {
                const solutionBox = document.createElement('pre');
                solutionBox.className = "ai-code";
                // Use the current solution instead of the next question's solution
                solutionBox.innerText = data.current_solution;
                console.log(solutionBox)
                document.getElementById('result').appendChild(solutionBox);
                showAISolutionButton.disabled = true;
            };
            document.getElementById('result').appendChild(showAISolutionButton);
        }
    });
}

// Function to update the streak display
function updateStreakDisplay(currentStreak, maxStreak, streakBroken, justSolved) {
    // Create streak container if it doesn't exist
    let streakContainer = document.getElementById('streak-container');
    if (!streakContainer) {
        streakContainer = document.createElement('div');
        streakContainer.id = 'streak-container';
        streakContainer.className = 'streak-container';
        
        // Create current streak box
        const currentStreakBox = document.createElement('div');
        currentStreakBox.className = 'streak-box current';
        currentStreakBox.innerHTML = `
            <div class="streak-value" id="current-streak">0</div>
            <div class="streak-label">Current Streak</div>
        `;
        
        // Create max streak box
        const maxStreakBox = document.createElement('div');
        maxStreakBox.className = 'streak-box max';
        maxStreakBox.innerHTML = `
            <div class="streak-value" id="max-streak">0</div>
            <div class="streak-label">Best Streak</div>
        `;
        
        streakContainer.appendChild(currentStreakBox);
        streakContainer.appendChild(maxStreakBox);
        
        // Insert at the top of the container, but after any daily challenge header if it exists
        const container = document.querySelector('.container');
        const dailyHeader = document.querySelector('.daily-challenge-header');
        
        if (dailyHeader) {
            container.insertBefore(streakContainer, dailyHeader.nextSibling);
        } else {
            container.insertBefore(streakContainer, container.firstChild);
        }
    }
    
    // Update streak values
    const currentStreakElement = document.getElementById('current-streak');
    const maxStreakElement = document.getElementById('max-streak');
    
    if (currentStreakElement && maxStreakElement) {
        // Remove any existing animation classes
        currentStreakElement.classList.remove('streak-increase', 'streak-broken');
        
        // Update the values
        currentStreakElement.textContent = currentStreak;
        maxStreakElement.textContent = maxStreak;
        
        // Add animation if streak changed
        if (justSolved && currentStreak > 0) {
            currentStreakElement.classList.add('streak-increase');
        } else if (streakBroken) {
            currentStreakElement.classList.add('streak-broken');
        }
    }
}

// Function to update daily streak display
function updateDailyStreakDisplay(currentStreak, maxStreak) {
    const currentStreakElement = document.getElementById('current-daily-streak');
    const maxStreakElement = document.getElementById('max-daily-streak');
    
    if (currentStreakElement && maxStreakElement) {
        currentStreakElement.textContent = currentStreak;
        maxStreakElement.textContent = maxStreak;
    }
}

// Function to save reflection
function saveReflection() {
    const reflection = document.getElementById('reflection-text').value;
    if (reflection.trim() === '') {
        alert("Please enter your reflection before saving.");
        return;
    }
    
    // For now, just acknowledge the save
    // In a future version, you could save this to localStorage or send to the server
    alert("Reflection saved! Thank you for your thoughts.");
    
    // Disable the button and textarea to indicate it's been saved
    document.getElementById('reflection-text').disabled = true;
    document.querySelector('.reflection-btn').disabled = true;
    document.querySelector('.reflection-btn').textContent = "Saved ✓";
}

// Enable Tab key for indentation
window.onload = function () {
    const editor = document.getElementById('code');
    editor.addEventListener('keydown', function (e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });
    
    // Set up mode toggle to persist between page loads
    const modeToggle = document.getElementById('mode-toggle');
    if (modeToggle) {
        const savedMode = localStorage.getItem('challengeMode');
        
        if (savedMode === 'true') {
            modeToggle.checked = true;
        } else {
            modeToggle.checked = false;
        }
    }
    
    // Initialize streak display
    const streakValue = parseInt(document.querySelector('meta[name="current-streak"]')?.content || '0');
    const maxStreakValue = parseInt(document.querySelector('meta[name="max-streak"]')?.content || '0');
    updateStreakDisplay(streakValue, maxStreakValue, false, false);
    
    // Initialize daily streak display if on daily challenge page
    const dailyStreakValue = parseInt(document.querySelector('meta[name="daily-streak"]')?.content || '0');
    const maxDailyStreakValue = parseInt(document.querySelector('meta[name="max-daily-streak"]')?.content || '0');
    if (document.querySelector('meta[name="is-daily-challenge"]')?.content === 'true') {
        updateDailyStreakDisplay(dailyStreakValue, maxDailyStreakValue);
    }
};