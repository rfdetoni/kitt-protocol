use kitt_protocol::{AuthenticatedFrame, Envelope, MAX_FRAME_BYTES, kinds};

#[test]
fn generated_envelopes_round_trip_across_payload_shapes() {
    for index in 0..256_u32 {
        let payload = serde_json::json!({
            "index": index,
            "text": format!("payload-{index}-á-🚀"),
            "nested": {
                "even": index % 2 == 0,
                "values": [index, index.saturating_add(1), index.saturating_mul(2)]
            }
        });
        let envelope = Envelope::new(
            if index % 2 == 0 {
                kinds::SYSTEM_PING_REQUEST
            } else {
                kinds::HUD_EVENT
            },
            payload,
        )
        .unwrap();
        let encoded = serde_json::to_vec(&envelope).unwrap();
        let decoded = Envelope::decode(&encoded).unwrap();
        assert_eq!(decoded, envelope);
    }
}

#[test]
fn deterministic_adversarial_bytes_never_escape_decoder_contract() {
    let mut state = 0x9e3779b97f4a7c15_u64;
    for length in 0..512_usize {
        let mut bytes = Vec::with_capacity(length);
        for _ in 0..length {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            bytes.push((state & 0xff) as u8);
        }
        let _ = Envelope::decode(&bytes);
        let _ = AuthenticatedFrame::decode(&bytes);
    }

    let oversized = vec![b' '; MAX_FRAME_BYTES + 1];
    assert_eq!(Envelope::decode(&oversized).unwrap_err(), "frame_too_large");
    assert_eq!(
        AuthenticatedFrame::decode(&oversized).err().as_deref(),
        Some("frame_too_large")
    );
}

#[test]
fn shared_invalid_wire_corpus_is_rejected() {
    let cases: Vec<String> =
        serde_json::from_str(include_str!("../fixtures/decoding-invalid.json")).unwrap();
    for raw in cases {
        assert!(Envelope::decode(raw.as_bytes()).is_err(), "accepted {raw}");
        let framed = format!("{{\"token\":\"test\",\"envelope\":{raw}}}");
        assert!(
            AuthenticatedFrame::decode(framed.as_bytes()).is_err(),
            "accepted {raw}"
        );
    }
    assert!(Envelope::decode(&[255]).is_err());
    assert!(Envelope::decode(br#"{"version":1,"id":"x","kind":"test","payload":null}"#).is_ok());
}
