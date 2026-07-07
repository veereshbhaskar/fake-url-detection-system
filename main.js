import { FakeURLDetector } from "./detector";

const detector = new FakeURLDetector();

const testUrls = [
    "https://google.com",
    "http://192.168.0.1/login",
    "https://secure-update-account.info/login",
    "https://bank-login.verify-user-security.com/update",
    "https://example.com"
];

testUrls.forEach(url => {
    const result = detector.analyze(url);
    console.log("=====================================");
    console.log("URL:", result.url);
    console.log("Risk Score:", result.riskScore);
    console.log("Is Fake:", result.isFake);
    console.log("Reasons:", result.reasons);
});
import {
    isIPAddress,
    hasAtSymbol,
    hasHyphenInDomain,
    countSubdomains,
    hasHTTPS,
    urlLength,
    containsSuspiciousWords,
    countSpecialCharacters,
    hasEncodedCharacters,
    hasDoubleSlashAfterProtocol
} from "./utils";

import { isBlacklisted } from "./blacklist";

export interface DetectionResult {
    url: string;
    riskScore: number;
    isFake: boolean;
    reasons: string[];
}

export class FakeURLDetector {

    analyze(url: string): DetectionResult {

        let riskScore = 0;
        let reasons: string[] = [];

        let parsed: URL;

        try {
            parsed = new URL(url);
        } catch {
            return {
                url,
                riskScore: 100,
                isFake: true,
                reasons: ["Invalid URL format"]
            };
        }

        const hostname = parsed.hostname;

        if (!hasHTTPS(url)) {
            riskScore += 10;
            reasons.push("No HTTPS protocol");
        }

        if (isIPAddress(hostname)) {
            riskScore += 20;
            reasons.push("IP address used instead of domain");
        }

        if (hasAtSymbol(url)) {
            riskScore += 15;
            reasons.push("@ symbol detected");
        }

        if (urlLength(url) > 75) {
            riskScore += 10;
            reasons.push("Long URL length");
        }

        if (hasHyphenInDomain(hostname)) {
            riskScore += 5;
            reasons.push("Hyphen in domain");
        }

        if (countSubdomains(hostname) > 2) {
            riskScore += 10;
            reasons.push("Too many subdomains");
        }

        if (containsSuspiciousWords(url)) {
            riskScore += 15;
            reasons.push("Suspicious keywords detected");
        }

        if (countSpecialCharacters(url) > 15) {
            riskScore += 5;
            reasons.push("Too many special characters");
        }

        if (hasEncodedCharacters(url)) {
            riskScore += 5;
            reasons.push("Encoded characters found");
        }

        if (hasDoubleSlashAfterProtocol(url)) {
            riskScore += 10;
            reasons.push("Double slash redirection trick");
        }

        if (isBlacklisted(hostname)) {
            riskScore += 40;
            reasons.push("Domain is blacklisted");
        }

        const isFake = riskScore >= 40;

        return {
            url,
            riskScore,
            isFake,
            reasons
        };
    }
}
