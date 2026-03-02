/** @odoo-module **/

import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PlayerDashboard extends Component {

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            teams: 0,
            matches: 0,
            seasons: 0,
            weeklyData: [],
            weekLabels: [],
        });

        onWillStart(async () => {

            // ===== Basic Counts =====
            this.state.teams = await this.orm.searchCount("football.team", []);
            this.state.matches = await this.orm.searchCount("football.match", []);
            this.state.seasons = await this.orm.searchCount("football.season", []);

            // ===== Get current season =====
            const seasons = await this.orm.searchRead(
                "football.season",
                [],
                ["start_date", "end_date"]
            );

            if (!seasons.length) {
                return;
            }

            const season = seasons[0];
            const seasonStart = new Date(season.start_date);

            // ===== Get matches of this season =====
            const matches = await this.orm.searchRead(
                "football.match",
                [["season_id", "=", season.id]],
                ["match_date"]
            );

            const grouped = {};

            matches.forEach(m => {

                const matchDate = new Date(m.match_date);

                const diffTime = matchDate - seasonStart;
                const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

                const week = Math.floor(diffDays / 7) + 1;

                grouped[week] = (grouped[week] || 0) + 1;
            });

            // ===== Fill 38 weeks (EPL standard) =====
            const totalWeeks = 38;

            for (let i = 1; i <= totalWeeks; i++) {
                this.state.weekLabels.push(`W${i}`);
                this.state.weeklyData.push(grouped[i] || 0);
            }
        });

        onMounted(() => {

            const ctx = document.getElementById("matchChart");

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: this.state.weekLabels,
                    datasets: [{
                        label: "Matches per Week",
                        data: this.state.weeklyData,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        });
    }
}

PlayerDashboard.template = "player_management.PlayerDashboard";

registry.category("actions").add(
    "player_management_dashboard",
    PlayerDashboard
);