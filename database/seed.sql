INSERT INTO contact_channel_reference (contact, channel_label, channel_group, priority_order)
VALUES
    ('cellular', 'Teléfono celular', 'digital', 1),
    ('telephone', 'Teléfono fijo', 'traditional', 2),
    ('unknown', 'Canal no informado', 'unknown', 3)
ON CONFLICT (contact) DO NOTHING;
